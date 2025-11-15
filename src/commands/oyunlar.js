const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('oyunlar')
        .setDescription('Sunucudaki kullanıcıların oynadığı oyunları gösterir.'),
    async execute(interaction) {
        await interaction.deferReply();

        const gameCounter = {};
        const { guild } = interaction;

        guild.members.cache.forEach(member => {
            if (member.user.bot) return;

            const activity = member.presence?.activities?.[0];
            if (!activity) return;

            let gameName = null;

            if (activity.type === 0) { // Playing
                gameName = `🎮 ${activity.name}`;
            } else if (activity.type === 1) { // Streaming
                gameName = `📺 ${activity.details || 'Canlı Yayın'}`;
            } else if (activity.type === 2) { // Listening (Spotify)
                gameName = `🎵 ${activity.details || activity.name}`;
            } else if (activity.name) {
                gameName = `🛠️ ${activity.name}`;
            }

            if (gameName) {
                gameCounter[gameName] = (gameCounter[gameName] || 0) + 1;
            }
        });

        if (Object.keys(gameCounter).length === 0) {
            return await interaction.followUp('❌ Şu anda kimse oyun oynamıyor veya bir aktivite yapmıyor.');
        }

        const sortedGames = Object.entries(gameCounter)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);

        const embed = new EmbedBuilder()
            .setColor('#0099ff')
            .setTitle('🎮 Sunucuda Oynanan Oyunlar')
            .setDescription(sortedGames.map(([game, count]) => `${game}: **${count}** kişi`).join('\n'))
            .setTimestamp();

        await interaction.followUp({ embeds: [embed] });
    }
};
