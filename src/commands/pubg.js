const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('pubg')
        .setDescription('PUBG istatistik takibini başlatır/durdurur.')
        .addStringOption(option =>
            option.setName('action')
                .setDescription('Başlatmak için start, durdurmak için stop')
                .setRequired(false)
                .addChoices(
                    { name: 'Start', value: 'start' },
                    { name: 'Stop', value: 'stop' }
                ))
        .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    async execute(interaction) {
        const action = interaction.options.getString('action') || 'start';

        // TODO: Implement PUBG tracking system
        
        if (action === 'start') {
            await interaction.reply({
                content: '🎮 PUBG takip özelliği henüz geliştirilme aşamasındadır.',
                ephemeral: true
            });
        } else {
            await interaction.reply({
                content: '⏹️ PUBG takip özelliği henüz geliştirilme aşamasındadır.',
                ephemeral: true
            });
        }
    }
};
