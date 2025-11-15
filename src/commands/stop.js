const { SlashCommandBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('stop')
        .setDescription('Stop music and disconnect bot'),
    async execute(interaction) {
        await interaction.reply({
            content: '⏹️ Müzik özelliği henüz geliştirilme aşamasındadır.',
            ephemeral: true
        });
    }
};
